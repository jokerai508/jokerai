import SwiftUI

struct FilesView: View {
    @State private var files: [String] = []
    @State private var selectedFile: String?
    
    var body: some View {
        NavigationStack {
            List(files, id: \.self) { file in
                Button(file) {
                    selectedFile = file
                }
            }
            .navigationTitle("Moomoo / Files")
            .task {
                await loadFiles()
            }
        }
    }
    
    private func loadFiles() async {
        // Placeholder file list. Replace with real Moomoo/email file access later.
        files = [
            "portfolio_report_2026.html",
            "market-trend.html",
            "malaysia-news.html",
            "hourly_stock_analysis.md"
        ]
    }
}

#Preview {
    NavigationStack {
        FilesView()
    }
}
