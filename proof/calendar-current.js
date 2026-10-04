(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1730d8b0663b86f4.js","sha256":"1730d8b0663b86f41a66ea9faad989c9cc792020bd66d5701c5b75d391747729","count":2183,"publishedAt":"2026-10-04T18:42:03Z","state":"calendar-state.json","stateSha256":"184c1bd625a2173c11caf591095e8cecbacef3f4b0bd82a5b87c2914a53b0a37","sourceState":"calendar-source-state.json","sourceStateSha256":"e310d00d98381d6f238dd7b5490612d7f702d42254685aee3a38e9084d56b3eb"});
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
