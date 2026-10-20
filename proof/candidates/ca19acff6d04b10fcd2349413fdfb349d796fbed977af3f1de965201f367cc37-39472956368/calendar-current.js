(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ca19acff6d04b10f.js","sha256":"ca19acff6d04b10fcd2349413fdfb349d796fbed977af3f1de965201f367cc37","count":2085,"publishedAt":"2026-10-20T18:16:13Z","state":"calendar-state.json","stateSha256":"1ae352f7a839a67c6913c55f19439d77018510c4a0ab999608dc308e3a5fd03a","sourceState":"calendar-source-state.json","sourceStateSha256":"5f8a4e1a4c2f2430b4aaeab712b42d1e5e61d374f70bb9efe3f278f5098be6c3"});
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
