(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e16aafbd17bd165a.js","sha256":"e16aafbd17bd165a5929892651753a23449ba842bc728beadeb0096b4c58797f","count":2179,"publishedAt":"2026-11-11T11:53:41Z","state":"calendar-state.json","stateSha256":"d2b522119ee9472296acb72c8c3c1d0688dfc94e57e207d50b6716ee76dcc445","sourceState":"calendar-source-state.json","sourceStateSha256":"da46b6cd36ba7de45caee7eb456571fa0c9e61bae5bd6820398c5752972952a9"});
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
