(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b0699c4db7ac82fb.js","sha256":"b0699c4db7ac82fb56c5297163d27429c7f62d6af8838cf226033520ac1be8ed","count":2055,"publishedAt":"2026-10-28T13:07:46Z","state":"calendar-state.json","stateSha256":"503323a794e03ccdbd79ddc6a2f68aa8d33b2bef54df714e175a9be78f4efd82","sourceState":"calendar-source-state.json","sourceStateSha256":"79f5922a412cd092011620d7f5400a8ace396ae2a41556f27bd46c81d5c9e266"});
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
