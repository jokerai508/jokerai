# JokerAI iOS App Draft

## What this is
A draft iOS app that provides:
1. Chat interface connected to oMLX (`gemma-4-e2b-it-4bit`)
2. Files button to access Moomoo/email files managed by Hermes

## Current state
- SwiftUI app scaffold with 2 tabs: Chat and Files
- Chat calls oMLX via HTTP (`localhost:8080` by default)
- Files tab shows placeholder list; real file access needs backend integration

## Next steps
1. Update `ChatViewModel.serverURL` to reachable oMLX endpoint
   - Same WiFi: `http://<mac-ip>:8080/v1/chat/completions`
   - ngrok tunnel: `https://<tunnel>.ngrok-free.dev/v1/chat/completions`
2. Implement file download/preview from Hermes-managed directories
3. Add Moomoo email sync viewer
4. Enroll in Apple Developer Program to sign and run on device

## Files
- `JokerAIApp.swift` - App entry
- `ContentView.swift` - Tab view
- `ChatView.swift` - Chat UI + oMLX client
- `FilesView.swift` - File browser placeholder
