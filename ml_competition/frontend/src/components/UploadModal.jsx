import { useState, useRef } from 'react';
import { uploadSubmission, evaluateSubmission } from '../api/client';

export default function UploadModal({ taskId, onClose, onSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const file = fileInputRef.current?.files[0];
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    try {
      // Upload file
      const uploadResult = await uploadSubmission(taskId, file);
      
      // Auto-evaluate
      const evalResult = await evaluateSubmission(uploadResult.submission_id, taskId);
      
      // Success callback
      if (onSuccess) {
        onSuccess(evalResult);
      }
      
      alert(`Submission evaluated!\nScore: ${evalResult.score}\nStatus: ${evalResult.status}`);
      onClose();
    } catch (err) {
      setError(err.message || 'Error submitting file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className="relative z-10 bg-white rounded-lg p-8 max-w-md w-full mx-4 shadow-xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-2xl text-gray-500 hover:text-gray-800"
        >
          ×
        </button>
        
        <h3 className="text-xl font-bold text-primary mb-6">
          Submit Solution for Question {taskId}
        </h3>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block font-semibold text-gray-700 mb-2">
              Select Python File
            </label>
            <label className="block p-6 text-center border-2 border-dashed border-primary rounded-lg bg-gray-50 cursor-pointer hover:bg-white transition-colors">
              <span className="text-gray-600">Click to browse or drag files here</span>
              <input
                ref={fileInputRef}
                type="file"
                accept=".py"
                className="hidden"
                required
              />
            </label>
          </div>
          
          <button
            type="submit"
            disabled={uploading}
            className="w-full py-3 bg-primary text-white font-semibold rounded hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Submitting...
              </span>
            ) : (
              'Submit'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
