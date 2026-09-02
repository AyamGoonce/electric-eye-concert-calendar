(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.91195e36722a7ec0.js","sha256":"91195e36722a7ec009dd8d0156da85af3bcbcc9e62550b5e126f9d70d40e7581","count":2171,"publishedAt":"2026-09-02T04:46:56Z","state":"calendar-state.json","stateSha256":"2a2be7226b76a9596aeceeb8f7c4fdeb99cc19321af83e3385602a0afdfd6352"});
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
