#include <QApplication>
#include <QMainWindow>
#include <QUrl>
#include <QWebEngineProfile>
#include <QWebEngineSettings>
#include <QWebEngineView>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    QApplication::setApplicationDisplayName(QStringLiteral("Smart Maintenance"));
    QApplication::setApplicationName(QStringLiteral("Smart Maintenance"));

    QMainWindow window;
    window.setWindowTitle(QStringLiteral("Smart Maintenance"));
    window.resize(390, 844);
    window.setMinimumSize(390, 844);
    window.setMaximumSize(430, 932);

    auto *view = new QWebEngineView(&window);
    view->page()->profile()->setHttpUserAgent(QStringLiteral(
        "Mozilla/5.0 (Linux; Android 13; LoongArch64 Demo) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Mobile Safari/537.36"));
    view->settings()->setAttribute(QWebEngineSettings::JavascriptEnabled, true);
    view->settings()->setAttribute(QWebEngineSettings::LocalStorageEnabled, true);
    view->setContextMenuPolicy(Qt::NoContextMenu);
    view->setUrl(QUrl(QStringLiteral("http://localhost:5173/")));

    window.setCentralWidget(view);
    window.show();
    return app.exec();
}
