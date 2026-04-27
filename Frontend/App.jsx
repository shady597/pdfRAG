import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, FileText, Loader2, Bot, User, CheckCircle2 } from 'lucide-react';

const RAGInterface = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [ingested, setIngested] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatContainerRef = useRef(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleFileUpload = async (e) => {
    const selectedFiles = Array.from(e.target.files);
    setUploading(true);

    for (const file of selectedFiles) {
      const formData = new FormData();
      formData.append('file', file
      );

      try {
        const response = await fetch('http://localhost:8000/upload', {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();
        if (response.ok) {
          setIngested(true);
          setFiles(prev => [...prev, file.name]);
        }
      } catch (error) {
        console.error("Upload failed:", error);
      }
    }
    setUploading(false);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      });
      const data = await response.json();
      
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Error: Could not connect to the server." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#0a0f1e] text-slate-200 font-sans">
      {/* Header */}
      <header className="p-4 border-b border-slate-800 bg-[#0d1425] flex justify-between items-center">
        <h1 className="text-xl font-bold tracking-tight text-blue-400">RAG Pipeline Explorer</h1>
        <div className="flex items-center gap-2">
          {ingested && <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full border border-green-800 flex items-center gap-1"><CheckCircle2 size={12}/> Knowledge Base Ready</span>}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden flex flex-col items-center justify-center relative">
        {!ingested && messages.length === 0 ? (
          <div className="max-w-md w-full p-8 border-2 border-dashed border-slate-700 rounded-2xl bg-[#0d1425] text-center transition-all hover:border-blue-500/50">
            <Upload className="mx-auto mb-4 text-blue-500" size={48} />
            <h2 className="text-lg font-semibold mb-2">Upload Source Documents</h2>
            <p className="text-slate-400 text-sm mb-6">Select PDF or TXT files.</p>
            <label className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg cursor-pointer transition-colors inline-flex items-center gap-2">
              {uploading ? <Loader2 className="animate-spin" size={18} /> : <FileText size={18} />}
              {uploading ? "Processing..." : "Select Files"}
              <input type="file" className="hidden" multiple onChange={handleFileUpload} accept=".pdf,.txt" />
            </label>
          </div>
        ) : (
          <div ref={chatContainerRef} className="w-full max-w-4xl h-full overflow-y-auto p-6 space-y-6 pb-32">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-blue-600' : 'bg-slate-700'}`}>
                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  <div className={`p-4 rounded-2xl ${msg.role === 'user' ? 'bg-blue-700 text-white' : 'bg-[#161f35] border border-slate-800'}`}>
                    <p className="text-sm leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="flex gap-3 items-center text-slate-500">
                  <Loader2 className="animate-spin" size={16} />
                  <span className="text-xs italic">AI is analyzing documents...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Full-width Chat Input */}
      <footer className="absolute bottom-0 w-full p-6 bg-gradient-to-t from-[#0a0f1e] via-[#0a0f1e] to-transparent">
        <form onSubmit={handleSendMessage} className="max-w-5xl mx-auto relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={ingested ? "Ask anything about your documents..." : "Upload a file to start chatting..."}
            disabled={!ingested && messages.length === 0}
            className="w-full bg-[#161f35] border border-slate-700 rounded-xl py-4 pl-6 pr-16 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </form>
        <p className="text-center text-[10px] text-slate-600 mt-3 uppercase tracking-widest font-medium">
          Powered by LangChain & PGVector
        </p>
      </footer>
    </div>
  );
};

export default RAGInterface;