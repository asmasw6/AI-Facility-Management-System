import React, { useRef, useState } from "react";
import ComplaintResults from "../components/ComplaintResults";

export default function Home() {
  // states
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [audioUrl, setAudioUrl] = useState(null);
  const [playingAudio, setPlayingAudio] = useState(false);

  const [activeAudioText, setActiveAudioText] = useState(null);
  // MediaRecorder reference
  const mediaRecorderRef = useRef(null);
  // Store recorded audio chunks
  const audioChunksRef = useRef([]);
  // Store currently playing audio
  const audioRef = useRef(null);
  // Temporary customer ID for testing.
  //const customerId = "6a9eda85521ecd1d215366de";

  // Submit Text Complaint
  const handleSubmit = async () => {
    if (!description.trim()) {
      setError("Please describe your issue.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    // remove previous audio URL
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/process-call/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            // ------------------------------------------------- *****
            //call_id: callId,
            text: description,
          }),
        },
      );

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(errorData.detail || "Failed to process complaint.");
      }

      const data = await response.json();

      setResult(data);
      setDescription("");
    } catch (err) {
      console.error("Text complaint error:", err);

      setError(
        err.message || "Something went wrong while processing your complaint.",
      );
    } finally {
      setLoading(false);
    }
  };

  // Start Recording

  const startRecording = async () => {
    try {
      setError("");
      setResult(null);

      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream);
      // store mediaRecorder
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Collect audio chunks if there is any data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // When recording stops
      mediaRecorder.onstop = async () => {
        try {
          // Create audio blob and collect all chunks in one audio file
          const audioBlob = new Blob(audioChunksRef.current, {
            type: "audio/webm",
          });

          // Stop microphone
          stream.getTracks().forEach((track) => track.stop());

          // Send audio to backend
          await sendVoice(audioBlob);
        } catch (err) {
          console.error("Recording processing error:", err);

          setError(err.message || "Failed to process the recorded audio.");
        }
      };

      // Start recording
      mediaRecorder.start();

      setRecording(true);
    } catch (err) {
      console.error("Microphone error:", err);

      setError(
        "Could not access your microphone. Please allow microphone permission.",
      );
    }
  };

  // Stop Recording
  const stopRecording = () => {
    if (!mediaRecorderRef.current) {
      // check the recorder is availaible or not
      return;
    }

    if (mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }

    setRecording(false);
  };

  // Send Voice Complaint
  const sendVoice = async (audioBlob) => {
    setLoading(true);
    setError("");
    setResult(null);

    // Remove previous audio
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }

    try {
      const formData = new FormData();
      // Audio file
      formData.append("audio", audioBlob, "complaint.webm");
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/calls/voice`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: formData,
        },
      );

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail || "Failed to process voice complaint.",
        );
      }

      const data = await response.json();

      setResult(data);
    } catch (err) {
      console.error("Voice complaint error:", err);

      setError(
        err.message ||
          "Something went wrong while processing your voice complaint.",
      );
    } finally {
      setLoading(false);
    }
  };

  // Play AI Response
  const playAIResponse = async (text) => {
    if (!text) return;

    try {
      setError("");
      setPlayingAudio(true);
      setActiveAudioText(text);

      // Stop currently playing audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      // Request TTS
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/calls/text-to-speech`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text,
          }),
        },
      );

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(errorData.detail || "Failed to generate speech.");
      }

      // Convert response to audio blob
      const blob = await response.blob();
      // Create temporary URL
      const url = URL.createObjectURL(blob);

      setAudioUrl(url);

      // Create audio object
      const audio = new Audio(url);
      audioRef.current = audio;

      // When audio finishes
      audio.onended = () => {
        setPlayingAudio(false);
        setActiveAudioText(null);
        audioRef.current = null;
        URL.revokeObjectURL(url);
        setAudioUrl(null);
      };

      // Play
      await audio.play();
    } catch (err) {
      console.error("TTS error:", err);
      setPlayingAudio(false);
      setActiveAudioText(null);
      setError(err.message || "Could not play the AI response.");
    }
  };

  // Stop AI Audio
  const stopAIResponse = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }

    setPlayingAudio(false);
  };

  // UI

  return (
    <div className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto max-w-3xl">
        {/* Header*/}

        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Facility Assistant
          </h1>

          <p className="mt-2 text-gray-600">
            Describe your issue by typing or using your voice. Our AI assistant
            will process your request.
          </p>
        </div>

        {/* Main Card*/}

        <div className="rounded-2xl bg-white p-8 shadow-sm">
          {/* Text Input*/}

          <div className="mb-6">
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Describe your issue
            </label>

            <textarea
              rows="6"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter Your Complaint Here..."
              disabled={recording || loading}
              className="w-full resize-none rounded-xl border border-gray-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-gray-100"
            />
          </div>

          {/* Buttons */}

          <div className="flex flex-col gap-3 sm:flex-row">
            {/* Submit Text */}

            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading || recording || !description.trim()}
              className="flex-1 rounded-xl bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
            >
              {loading ? "Processing..." : "Submit Complaint"}
            </button>

            {/* Voice Button */}

            {!recording ? ( // recording === false
              <button
                type="button"
                onClick={startRecording}
                disabled={loading}
                className="flex-1 rounded-xl border border-gray-300 bg-white px-6 py-3 font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:bg-gray-100"
              >
                🎙️ Record Voice
              </button>
            ) : (
              // recording === true
              <button
                type="button"
                onClick={stopRecording}
                className="flex-1 rounded-xl bg-red-600 px-6 py-3 font-medium text-white transition hover:bg-red-700"
              >
                ⏹ Stop Recording
              </button>
            )}
          </div>

          {/* Recording Status*/}

          {recording && (
            <div className="mt-4 rounded-xl bg-red-50 p-4 text-center">
              <div className="flex items-center justify-center gap-2">
                <span className="h-3 w-3 animate-pulse rounded-full bg-red-500"></span>

                <p className="font-medium text-red-700">Recording...</p>
              </div>

              <p className="mt-1 text-sm text-red-600">
                Speak clearly, then press Stop Recording.
              </p>
            </div>
          )}

          {/*Error */}

          {error && (
            <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Loading*/}

          {loading && (
            <div className="mt-6 rounded-xl bg-blue-50 p-4 text-center">
              <p className="text-sm font-medium text-blue-700">
                AI is processing your request...
              </p>
            </div>
          )}

          {/* Result */}
          {result && !loading && (
            <>
              {/* Original user message */}
              {(Array.isArray(result)
                ? result[0]?.transcript
                : result.transcript) && (
                <div className="mt-8 rounded-xl bg-gray-50 p-5">
                  <p className="text-sm font-semibold text-gray-500">
                    Your message
                  </p>

                  <p className="mt-2 text-gray-800">
                    {Array.isArray(result)
                      ? result[0]?.transcript
                      : result.transcript}
                  </p>
                </div>
              )}

              {/* Individual complaint result cards */}
              <ComplaintResults
                result={result}
                playingAudio={playingAudio}
                activeAudioText={activeAudioText}
                onPlayAudio={playAIResponse}
                onStopAudio={stopAIResponse}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
