import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            ChatView()
                .tabItem {
                    Label("Chat", systemImage: "message.fill")
                }
                .tag(0)
            
            FilesView()
                .tabItem {
                    Label("Files", systemImage: "folder.fill")
                }
                .tag(1)
        }
    }
}

#Preview {
    ContentView()
}
