export default function ChatMessage({ message }) {
  return (
    <div className={`message ${message.role}`}>
      <div className="bubble">{message.content}</div>
    </div>
  );
}