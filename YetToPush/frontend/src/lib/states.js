export const STATES = {
  idle: { label: 'Idle', hint: 'Tap the mic or type a message', color: '#60a5fa' },
  listening: { label: 'Listening', hint: 'Speak now. I stop when you pause.', color: '#22d3ee' },
  thinking: { label: 'Thinking', hint: 'Working on it…', color: '#a78bfa' },
  speaking: { label: 'Speaking', hint: 'Tap the mic to interrupt', color: '#c084fc' },
  error: { label: 'Error', hint: 'Something went wrong. Try again.', color: '#f87171' },
}
export const VOICES = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'fable', 'nova', 'onyx', 'sage', 'shimmer']
export const LANGUAGES = [['en-IN', 'English (India)'], ['en-US', 'English (US)'], ['en-GB', 'English (UK)'], ['hi-IN', 'Hindi']]
export const PROMPTS = ['What can you do?', 'Open YouTube', 'Open GitHub', 'Tell me a fun fact', 'Explain AI in simple words']
