import React from 'react';

const ChatMessage = ({ message }) => {
  return (
    <div
      className={`chat-message ${
        message.sender === 'user' ? 'bg-blue-100' : 'bg-gray-100'
      } p-3 rounded-lg shadow-md`}
    >
      <span className="font-bold">{message.sender}:</span>{' '}
      <span>{message.content}</span>
      <span className="block text-xs text-gray-500">{message.timestamp}</span>
    </div>
  );
};

export default ChatMessage;
