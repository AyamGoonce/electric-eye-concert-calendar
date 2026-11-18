(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f2822b7b5b0fc425.js","sha256":"f2822b7b5b0fc425560eaf43b46386895016b05c176898e907d1ee9e496b66af","count":2094,"publishedAt":"2026-11-18T01:00:08Z","state":"calendar-state.json","stateSha256":"deabe068e8822c4d9f0e13c4bac26cf180ff79dbbcc6044d0d8356c849da1d6f","sourceState":"calendar-source-state.json","sourceStateSha256":"d766f0958dd02d942143eec887df22ab34ea8a658ed8098378276e6584dd6dc0"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
