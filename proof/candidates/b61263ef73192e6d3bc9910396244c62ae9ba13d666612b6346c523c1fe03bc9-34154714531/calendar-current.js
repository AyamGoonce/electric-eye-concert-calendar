(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b61263ef73192e6d.js","sha256":"b61263ef73192e6d3bc9910396244c62ae9ba13d666612b6346c523c1fe03bc9","count":2412,"publishedAt":"2026-09-07T19:22:25Z","state":"calendar-state.json","stateSha256":"2ac10ada84994805b14249045556183fdffe2bfcf1e8659a3aadbac8e6729e09"});
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
