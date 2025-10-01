async function getAccessToken() {
    try {
        const res = await fetch('/api/aec/token');
        const data = await res.json();
        return data;
    } catch (err) {
        console.error("Token fetch failed:", err);
        alert("Could not obtain access token.");
        return null;
    }
}

export function initViewer(container, urn) {
    return new Promise(function (resolve, reject) {
        Autodesk.Viewing.Initializer({ env: 'AutodeskProduction',
            getAccessToken: function(onTokenReady) {
                getAccessToken().then(data => {
                    if (data) {
                        onTokenReady(data, 3600);
                    } else {
                        console.error("Failed to obtain valid token", data);
                    }
                }).catch(err => {
                    console.error("Token fetch failed:", err);
                });
            }
            }, function () {
            const config = {
                extensions: ['Autodesk.DocumentBrowser']
            };
            const viewer = new Autodesk.Viewing.GuiViewer3D(container, config);
            viewer.start();
            viewer.setTheme('light-theme');
            resolve(viewer);
        });
    });
}

export function loadModel(viewer, urn) {
    return new Promise((resolve, reject) => {
        function onDocumentLoadSuccess(doc) {
            const defaultModel = doc.getRoot().getDefaultGeometry();
            viewer.loadDocumentNode(doc, defaultModel).then(() => {
                viewer.setSelectionMode(Autodesk.Viewing.SelectionMode.MIXED);
                enableSelection(viewer);
                resolve(viewer);
            }).catch(err => reject(err));
        }

        function onDocumentLoadFailure(code, message, errors) {
            console.error('Document Load Failed:', code, message, errors);
            reject({ code, message, errors });
        }

        Autodesk.Viewing.Document.load('urn:' + urn, onDocumentLoadSuccess, onDocumentLoadFailure);
    });
}

function enableSelection(viewer) {
    viewer.addEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, (event) => {
        const dbIds = event.dbIdArray;
        if (!dbIds || dbIds.length === 0) return;

        dbIds.forEach(dbId => {
            console.log("선택된 객체 DB ID:", dbId);

            if (window.FlutterChannel) {
                window.FlutterChannel.postMessage(dbId.toString());
            }
        });
    });
}