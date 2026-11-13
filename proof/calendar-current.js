(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ca8bd03a5b56b322.js","sha256":"ca8bd03a5b56b322d115049d8392bfea68803d9aab98e43de4abdf239097d582","count":2086,"publishedAt":"2026-11-13T01:53:56Z","state":"calendar-state.json","stateSha256":"26adbbc1e0f86ae4d33673f89e44cbd4d7cea6f8885ebeecb8c13a43eb808e01","sourceState":"calendar-source-state.json","sourceStateSha256":"1e926ce060745ce00e5b71da523cd7153f3ef01a9fe2520e46e1715417fff257"});
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
