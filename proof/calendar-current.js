(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b52e8fafaf2153fb.js","sha256":"b52e8fafaf2153fbf5221843385de82d9485c9167558dbad483d5c70ab247f0e","count":2146,"publishedAt":"2026-10-13T06:54:03Z","state":"calendar-state.json","stateSha256":"c23351d563a22ef929088868f164ff50d9329552e3654ba88727a9ccc2565fa9","sourceState":"calendar-source-state.json","sourceStateSha256":"5ea93216f5ad324a8f685a7ff2963564077b22d02c7ed3a1708f3e93895b7567"});
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
