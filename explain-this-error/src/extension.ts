import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {

    console.log('Explain This Error extension is now active!');

    const disposable = vscode.commands.registerCommand(
        'explain-this-error.explainError',
        async () => {

            const editor = vscode.window.activeTextEditor;

            if (!editor) {
                vscode.window.showErrorMessage(
                    'No active editor found.'
                );
                return;
            }

            const document = editor.document;
            const selection = editor.selection;

            // Get selected text
            let errorText = document.getText(selection);

            // If nothing is selected, use the current line
            if (!errorText.trim()) {
                errorText = document.lineAt(selection.active.line).text;
            }

            if (!errorText.trim()) {
                vscode.window.showWarningMessage(
                    'Please select an error or place your cursor on the error line.'
                );
                return;
            }

            // Get file information
            const fileName = document.fileName;
            const language = document.languageId;

            // Get some surrounding code
            const startLine = Math.max(0, selection.active.line - 5);
            const endLine = Math.min(
                document.lineCount - 1,
                selection.active.line + 5
            );

            const relevantCode = document.getText(
                new vscode.Range(
                    startLine,
                    0,
                    endLine,
                    document.lineAt(endLine).text.length
                )
            );

            // Show progress while communicating with FastAPI
            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Explaining error...',
                    cancellable: false
                },
                async () => {

                    try {

                        const response = await fetch(
                            'http://127.0.0.1:8000/explain-error',
                            {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    error: errorText,
                                    code: relevantCode,
                                    file_name: fileName,
                                    language: language
                                })
                            }
                        );

                        if (!response.ok) {
                            throw new Error(
                                `Backend returned ${response.status}`
                            );
                        }

                        const result:any = await response.json();

                        const explanation =
                            result.explanation || 'No explanation returned.';

                        const cause =
                            result.cause || 'No cause information returned.';

                        const fix =
                            result.fix || 'No suggested fix returned.';

                        // Display result
                        const message =
                            `What happened:\n${explanation}\n\n` +
                            `Cause:\n${cause}\n\n` +
                            `Suggested fix:\n${fix}`;

                        vscode.window.showInformationMessage(
                            message,
                            { modal: true }
                        );

                    } catch (error) {

                        console.error(
                            'Error communicating with backend:',
                            error
                        );

                        vscode.window.showErrorMessage(
                            'Could not connect to the Explain This Error backend. ' +
                            'Make sure your FastAPI server is running.'
                        );
                    }
                }
            );
        }
    );

    context.subscriptions.push(disposable);
}

export function deactivate() {}
