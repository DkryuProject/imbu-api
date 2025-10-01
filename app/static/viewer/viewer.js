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

// Forge Viewer 초기화
export function initViewer(container, urn) {
    return new Promise(function (resolve, reject) {
        Autodesk.Viewing.Initializer({
            env: 'AutodeskProduction',
            getAccessToken: function(onTokenReady) {
                getAccessToken().then(data => {
                    if (data) onTokenReady(data, 3600);
                    else console.error("Failed to obtain valid token", data);
                }).catch(err => console.error("Token fetch failed:", err));
            }
        }, function () {
            const config = {
                extensions: ['Autodesk.DocumentBrowser', 'Autodesk.Geolocation']
            };
            const viewer = new Autodesk.Viewing.GuiViewer3D(container, config);
            viewer.start();
            viewer.setTheme('light-theme');

            // Custom Overlay Scene 생성
            const overlayName = 'gps-scene';
            if (!viewer.overlays.hasScene(overlayName)) {
                viewer.overlays.addScene(overlayName);
            }

            // Geolocation 확장 가져오기
            const geoExt = viewer.getExtension('Autodesk.Geolocation');
            if (!geoExt || !geoExt.hasGeolocationData()) {
                console.warn("모델에 GPS 정보가 없습니다!");
            }

            // 선택 이벤트 활성화
            enableSelection(viewer, geoExt, overlayName);

            resolve(viewer);
        });
    });
}

// 모델 로드
export function loadModel(viewer, urn) {
    return new Promise((resolve, reject) => {
        function onDocumentLoadSuccess(doc) {
            const defaultModel = doc.getRoot().getDefaultGeometry();
            viewer.loadDocumentNode(doc, defaultModel).then(() => {
                viewer.setSelectionMode(Autodesk.Viewing.SelectionMode.MIXED);
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

// 선택 이벤트와 GPS 마커 표시
function enableSelection(viewer, geoExt, overlayName) {

    viewer.addEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, (event) => {
        const dbIds = event.dbIdArray;
        if (!dbIds || dbIds.length === 0) return;

        // 기존 마커 제거
        viewer.overlays.removeScene(overlayName);
        viewer.overlays.addScene(overlayName);

        dbIds.forEach(dbId => {
            const instanceTree = viewer.model.getData().instanceTree;
            if (!instanceTree) return;

            const fragIds = [];
            instanceTree.enumNodeFragments(dbId, fId => fragIds.push(fId));
            if (fragIds.length === 0) return;

            fragIds.forEach(fragId => {
                const fragList = viewer.model.getFragmentList();

                // Bounding Box 중심 좌표 계산
                const bounds = new THREE.Box3();
                fragList.getWorldBounds(fragId, bounds);
                const center = bounds.getCenter(new THREE.Vector3());

                // 빨간색 마커 생성
                const geom = new THREE.SphereGeometry(1, 16, 16);
                const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
                const sphere = new THREE.Mesh(geom, material);
                sphere.position.set(center.x, center.y, center.z);
                viewer.overlays.addMesh(sphere, overlayName);

                // GPS 좌표 변환
                let gps = null;
                if (geoExt && geoExt.hasGeolocationData()) {
                    gps = geoExt.lmvToLonLat({ x: center.x, y: center.y });
                }

                if (!gps) {
                    console.warn(`DB ID ${dbId} 선택됨: GPS 정보 없음`);
                } else {
                    console.log(`DB ID ${dbId} 선택됨, GPS:`, gps);
                }

                // Flutter로 전송
                if (window.FlutterChannel) {
                    window.FlutterChannel.postMessage(dbId.toString());
                }
            });
        });
    });
}
