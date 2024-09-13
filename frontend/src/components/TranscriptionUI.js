import React, { useState } from 'react';
import axios from 'axios';
import { ArrowUpTrayIcon, DocumentTextIcon, ClipboardDocumentIcon, PrinterIcon } from '@heroicons/react/24/solid';
import ReactMarkdown from 'react-markdown';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "./ui/accordion"
import { Button } from "./ui/button"
import { Input } from "./ui/input"

const TranscriptionUI = () => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [transcript, setTranscript] = useState('');
  const [meetingMinutes, setMeetingMinutes] = useState('');
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const handleFileChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);
    setTranscript('');
    setMeetingMinutes('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/meetings/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          setUploadProgress(percentCompleted);
        },
      });

      setTranscript(response.data.transcript);
      setMeetingMinutes(response.data.meeting_minutes);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('Axios Error:', error.message);
        console.error('Response data:', error.response?.data);
        console.error('Response status:', error.response?.status);
        console.error('Response headers:', error.response?.headers);

        if (error.response?.status === 404) {
          setError('API endpoint not found. Please check your server configuration.');
        } else if (error.response?.status === 400) {
          setError('Invalid file type or bad request. Please try again with a different file.');
        } else if (error.response?.status === 500) {
          setError('Server error. Please try again later.');
        } else {
          setError(`Error: ${error.message}`);
        }
      } else {
        console.error('Unexpected error:', error);
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleCopyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Copied to clipboard!');
    });
  };

  const handlePrint = () => {
    window.print();
  };

  const highlightSearchTerm = (text) => {
    if (!searchTerm) return text;
    const parts = text.split(new RegExp(`(${searchTerm})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === searchTerm.toLowerCase()
        ? <mark key={i} className="bg-yellow-300 text-black">{part}</mark>
        : part
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-4xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-gray-800 shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-3xl mx-auto">
            <div className="divide-y divide-gray-700">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-300 sm:text-lg sm:leading-7">
                <h2 className="text-3xl font-extrabold text-white">Audio Transcription and Meeting Minutes</h2>
                <p className="text-gray-400">Upload an audio file to get started</p>

                <div className="flex items-center justify-center w-full">
                  <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-700 hover:bg-gray-600">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <ArrowUpTrayIcon className="w-10 h-10 mb-3 text-gray-400" />
                      <p className="mb-2 text-sm text-gray-400"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                      <p className="text-xs text-gray-400">WAV, MP3 or FLAC (MAX. 800x400px)</p>
                    </div>
                    <input id="dropzone-file" type="file" className="hidden" onChange={handleFileChange} accept="audio/*" />
                  </label>
                </div>

                {file && (
                  <p className="text-sm text-gray-400">Selected file: {file.name}</p>
                )}

                {error && (
                  <p className="text-sm text-red-400">{error}</p>
                )}

                <Button
                  onClick={handleUpload}
                  disabled={!file || isUploading}
                  className="w-full"
                >
                  {isUploading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Uploading... {uploadProgress}%
                    </>
                  ) : (
                    <>
                      <DocumentTextIcon className="w-5 h-5 mr-2" />
                      Start Transcription and Generate Minutes
                    </>
                  )}
                </Button>

                {(transcript || meetingMinutes) && (
                  <>
                    <div className="flex justify-between items-center mt-6">
                      <Input
                        type="text"
                        placeholder="Search in minutes and transcript..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-2/3"
                      />
                      <Button onClick={() => handleCopyToClipboard(meetingMinutes)} className="ml-2">
                        <ClipboardDocumentIcon className="w-5 h-5 mr-2" />
                        Copy
                      </Button>
                      <Button onClick={handlePrint} className="ml-2">
                        <PrinterIcon className="w-5 h-5 mr-2" />
                        Print
                      </Button>
                    </div>
                    <Tabs defaultValue="minutes" className="w-full mt-6">
                      <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="minutes">Meeting Minutes</TabsTrigger>
                        <TabsTrigger value="transcript">Full Transcript</TabsTrigger>
                      </TabsList>
                      <TabsContent value="minutes" className="mt-4">
                        <h3 className="text-xl font-medium text-white mb-4">Meeting Minutes:</h3>
                        <Accordion type="single" collapsible className="w-full">
                          {meetingMinutes.split('\n\n').map((section, index) => {
                            const [title, ...content] = section.split('\n');
                            return (
                              <AccordionItem value={`item-${index}`} key={index}>
                                <AccordionTrigger>{highlightSearchTerm(title)}</AccordionTrigger>
                                <AccordionContent>
                                  <ReactMarkdown className="text-gray-300 prose prose-invert max-w-none">
                                    {highlightSearchTerm(content.join('\n'))}
                                  </ReactMarkdown>
                                </AccordionContent>
                              </AccordionItem>
                            );
                          })}
                        </Accordion>
                      </TabsContent>
                      <TabsContent value="transcript" className="mt-4">
                        <h3 className="text-xl font-medium text-white mb-4">Full Transcript:</h3>
                        <div className="mt-2 p-4 bg-gray-700 rounded-lg max-h-96 overflow-y-auto">
                          <p className="text-gray-300 whitespace-pre-wrap">{highlightSearchTerm(transcript)}</p>
                        </div>
                      </TabsContent>
                    </Tabs>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TranscriptionUI;