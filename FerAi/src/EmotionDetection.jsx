import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';
import ChatWindow from './ChatWindow';

const LiveEmotionDetection = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [emotionResult, setEmotionResult] = useState('');
  const [isCapturing, setIsCapturing] = useState(false);
  const [error, setError] = useState(null);
  const [serverStatus, setServerStatus] = useState('Checking...');
  const [currentEmotion, setCurrentEmotion] = useState('neutral');

  // Server status check
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const response = await axios.get('http://localhost:5000/health');
        setServerStatus('Server Ready');
        setError(null);
      } catch (error) {
        if (error.response && error.response.status === 503) {
          setServerStatus('Server Not Ready');
          setError(error.response.data.message || 'Server is not ready. Please try again later.');
        } else {
          setServerStatus('Server Unreachable');
          setError('Unable to connect to the server. Please check your connection.');
        }
      }
    };

    checkServerStatus();
    const interval = setInterval(checkServerStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  // Camera setup
  useEffect(() => {
    let stream = null;
    const startCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing the camera:", err);
        setError("Failed to access the camera. Please make sure it's connected and you've granted permission.");
      }
    };

    startCamera();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      context.drawImage(videoRef.current, 0, 0, 640, 480);
      return canvasRef.current.toDataURL('image/jpeg');
    }
    return null;
  };

  const predictEmotion = async () => {
    if (serverStatus !== 'Server Ready') {
      setError('Server is not ready. Please wait and try again.');
      return;
    }
  
    const imageData = captureImage();
    if (!imageData) return;
  
    const blob = await fetch(imageData).then(res => res.blob());
    const formData = new FormData();
    formData.append('image', blob, 'captured_image.jpg');
  
    try {
      const response = await axios.post('http://localhost:5000/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      if (response.data && response.data.emotions && response.data.emotions.length > 0) {
        const topEmotion = response.data.emotions[0];
        setEmotionResult(`${topEmotion.emotion} (${(topEmotion.confidence * 100).toFixed(1)}%)`);
        setCurrentEmotion(topEmotion.emotion.toLowerCase());
      } else if (response.data && response.data.emotion) {
        setEmotionResult(response.data.emotion);
        setCurrentEmotion(response.data.emotion.toLowerCase());
      } else {
        setEmotionResult('No emotion detected');
        setCurrentEmotion('neutral');
      }
      
      setError(null);
    } catch (error) {
      console.error('Error during emotion prediction:', error);
      setError('An error occurred while detecting emotion. Please try again.');
      setEmotionResult('');
    }
  };

  const toggleCapture = () => {
    if (serverStatus !== 'Server Ready') {
      setError('Server is not ready. Please wait for the server to be ready before starting capture.');
      return;
    }
    setIsCapturing(!isCapturing);
    setError(null);
    setEmotionResult("");
  };

  useEffect(() => {
    let interval;
    if (isCapturing && serverStatus === 'Server Ready') {
      interval = setInterval(predictEmotion, 1000);
    }
    return () => clearInterval(interval);
  }, [isCapturing, serverStatus]);

  const getStatusIcon = () => {
    switch (serverStatus) {
      case 'Server Ready':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'Checking...':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
  };

  

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              {/* Header */}
              <div className="border-b border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <h1 className="text-xl font-semibold text-gray-800">Live Emotion Detection</h1>
                  <div className="flex items-center gap-2">
                    {getStatusIcon()}
                    <span className={`text-sm font-medium ${
                      serverStatus === 'Server Ready' ? 'text-green-600' :
                      serverStatus === 'Checking...' ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {serverStatus}
                    </span>
                  </div>
                </div>
              </div>

              {/* Video Feed */}
              <div className="p-4">
                <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden">
                  <video
                    ref={videoRef}
                    autoPlay
                    className="w-full h-full object-cover"
                  />
                  <canvas
                    ref={canvasRef}
                    className="hidden"
                    width={640}
                    height={480}
                  />
                </div>
              </div>

              {/* Controls and Results */}
              <div className="p-4 bg-gray-50">
                <div className="flex flex-col gap-4">
                  <button
                    onClick={toggleCapture}
                    disabled={serverStatus !== 'Server Ready'}
                    className={`px-6 py-2 rounded-lg font-medium transition-all ${
                      isCapturing
                        ? 'bg-red-500 hover:bg-red-600 text-white'
                        : 'bg-blue-500 hover:bg-blue-600 text-white'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {isCapturing ? 'Stop Capturing' : 'Start Capturing'}
                  </button>

                  {error && (
                    <div className="flex items-center gap-2 p-3 rounded-lg bg-red-100 text-red-600">
                      <AlertCircle className="w-5 h-5" />
                      <span>{error}</span>
                    </div>
                  )}

                  {emotionResult && (
                    <div className="flex items-center justify-between p-4 rounded-lg bg-blue-50">
                      <span className="text-lg font-medium text-blue-900">Current Emotion:</span>
                      <span className="text-lg font-bold text-blue-600">{emotionResult}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Chat Window */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg h-full">
              <ChatWindow currentEmotion={currentEmotion} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveEmotionDetection;