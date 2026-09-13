(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b1ebb735c564c839.js","sha256":"b1ebb735c564c8398e9c185a13ec1b014cfe6d200787d45c49f73d71ca0bb1fb","count":2442,"publishedAt":"2026-09-13T04:58:01Z","state":"calendar-state.json","stateSha256":"651da44bf0de87b353aa18454d59bd04c619ff1150f1b0a96f6b488fd1450cef"});
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
