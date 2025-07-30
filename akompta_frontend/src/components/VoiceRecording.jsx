import React, { useState, useRef } from 'react';
import { Mic, StopCircle, Send, X, Loader } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const VoiceRecording = ({ isOpen, onClose }) => {
  const { authenticatedFetch, API_BASE_URL } = useAuth();
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioURL, setAudioURL] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [aiResponse, setAiResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  if (!isOpen) return null;

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        setAudioURL(URL.createObjectURL(blob));
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setTranscript('');
      setAiResponse(null);
      setAudioBlob(null);
      setAudioURL(null);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Impossible de démarrer l\'enregistrement. Assurez-vous que le microphone est autorisé.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const sendAudioForProcessing = async () => {
    if (!audioBlob) return;

    setLoading(true);
    try {
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64data = reader.result.split(',')[1];

        const response = await authenticatedFetch(`${API_BASE_URL}/voice/process/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ audio_base64: base64data }),
        });

        if (response.ok) {
          const data = await response.json();
          setTranscript(data.transcript);
          setAiResponse(data.ai_response);
          // Here you would typically dispatch an action based on ai_response.intent
          // e.g., if (data.ai_response.intent === 'record_sale') navigate('/sales');
        } else {
          const errorData = await response.json();
          console.error('Failed to process voice command:', errorData);
          setAiResponse({ error: errorData.error || 'Erreur lors du traitement de la commande vocale.' });
        }
      };
    } catch (error) {
      console.error('Error sending audio:', error);
      setAiResponse({ error: 'Erreur lors de l\'envoi de l\'audio.' });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    stopRecording();
    setAudioBlob(null);
    setAudioURL(null);
    setTranscript('');
    setAiResponse(null);
    setLoading(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 shadow-xl w-full max-w-md relative">
        <button onClick={handleClose} className="absolute top-3 right-3 text-gray-500 hover:text-gray-700">
          <X size={24} />
        </button>
        <h2 className="text-xl font-bold text-center mb-4">Commande Vocale AI</h2>

        <div className="flex justify-center items-center mb-6">
          {!isRecording && !audioURL && (
            <button
              onClick={startRecording}
              className="w-20 h-20 rounded-full bg-akompta-primary text-white flex items-center justify-center shadow-lg hover:bg-akompta-dark transition-colors"
            >
              <Mic size={32} />
            </button>
          )}
          {isRecording && (
            <button
              onClick={stopRecording}
              className="w-20 h-20 rounded-full bg-red-500 text-white flex items-center justify-center shadow-lg hover:bg-red-600 transition-colors animate-pulse"
            >
              <StopCircle size={32} />
            </button>
          )}
          {audioURL && !isRecording && (
            <audio controls src={audioURL} className="w-full"></audio>
          )}
        </div>

        {audioURL && !isRecording && (
          <div className="flex justify-center mb-4">
            <button
              onClick={sendAudioForProcessing}
              disabled={loading}
              className="btn-primary flex items-center justify-center"
            >
              {loading ? <Loader className="animate-spin mr-2" size={20} /> : <Send size={20} className="mr-2" />}
              {loading ? 'Traitement...' : 'Envoyer la commande'}
            </button>
          </div>
        )}

        {transcript && (
          <div className="mt-4 p-3 bg-gray-100 rounded-lg">
            <p className="text-sm font-semibold text-gray-700">Transcription:</p>
            <p className="text-gray-800 italic">"{transcript}"</p>
          </div>
        )}

        {aiResponse && (
          <div className="mt-4 p-3 bg-gray-100 rounded-lg">
            <p className="text-sm font-semibold text-gray-700">Réponse AI:</p>
            <pre className="text-gray-800 text-xs whitespace-pre-wrap">{JSON.stringify(aiResponse, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceRecording;


