import SwiftUI

struct ChatMessage: Identifiable {
    let id = UUID()
    let text: String
    let isUser: Bool
}

class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var inputText = ""
    @Published var isLoading = false
    
    // Change this to your actual oMLX endpoint
    var serverURL: String = "http://localhost:8080/v1/chat/completions"
    
    private func buildRequestBody(for text: String) -> [String: Any] {
        return [
            "model": "mlx-community/gemma-4-e2b-it-4bit",
            "messages": [
                ["role": "user", "content": text]
            ],
            "chat_template_kwargs": [
                "enable_thinking": false
            ]
        ]
    }
    
    func sendMessage() {
        let trimmed = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        
        messages.append(ChatMessage(text: trimmed, isUser: true))
        inputText = ""
        isLoading = true
        
        guard let url = URL(string: serverURL) else {
            messages.append(ChatMessage(text: "Invalid server URL.", isUser: false))
            isLoading = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: buildRequestBody(for: trimmed), options: [])
        } catch {
            messages.append(ChatMessage(text: "Failed to build request: \(error.localizedDescription)", isUser: false))
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                guard let self = self else { return }
                self.isLoading = false
                
                if let error = error {
                    self.messages.append(ChatMessage(text: "Network error: \(error.localizedDescription)", isUser: false))
                    return
                }
                
                guard let data = data else {
                    self.messages.append(ChatMessage(text: "No response data.", isUser: false))
                    return
                }
                
                do {
                    if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any],
                       let choices = json["choices"] as? [[String: Any]],
                       let first = choices.first,
                       let message = first["message"] as? [String: Any],
                       let content = message["content"] as? String {
                        self.messages.append(ChatMessage(text: content, isUser: false))
                    } else {
                        self.messages.append(ChatMessage(text: "Unexpected response format.", isUser: false))
                    }
                } catch {
                    self.messages.append(ChatMessage(text: "Failed to parse response: \(error.localizedDescription)", isUser: false))
                }
            }
        }.resume()
    }
}

struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                ScrollViewReader { proxy in
                    ScrollView {
                        VStack(spacing: 12) {
                            ForEach(viewModel.messages) { msg in
                                ChatBubble(message: msg)
                                    .id(msg.id)
                            }
                            if viewModel.isLoading {
                                ProgressView()
                                    .padding()
                            }
                        }
                        .padding(.horizontal)
                        .padding(.top, 8)
                    }
                    .onChange(of: viewModel.messages) { _ in
                        if let last = viewModel.messages.last {
                            proxy.scrollTo(last.id, anchor: .bottom)
                        }
                    }
                }
                
                HStack(spacing: 8) {
                    TextField("Message...", text: $viewModel.inputText)
                        .textFieldStyle(.roundedBorder)
                        .onSubmit(viewModel.sendMessage)
                    
                    Button("Send") {
                        viewModel.sendMessage()
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(viewModel.isLoading || viewModel.inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
                .padding()
            }
            .navigationTitle("Joker AI")
        }
    }
}

struct ChatBubble: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.isUser { Spacer() }
            Text(message.text)
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
                .background(message.isUser ? Color.accentColor : Color(.secondarySystemBackground))
                .foregroundStyle(message.isUser ? .white : .primary)
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                .frame(maxWidth: 260, alignment: message.isUser ? .trailing : .leading)
            if !message.isUser { Spacer() }
        }
    }
}

#Preview {
    NavigationStack {
        ChatView()
    }
}
