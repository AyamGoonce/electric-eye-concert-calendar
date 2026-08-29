(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b8ed006f2ede7666.js","sha256":"b8ed006f2ede76665601fa8649581071936d22da09627c1c13a2e32e23d927bc","count":2066,"publishedAt":"2026-08-29T12:17:42Z","state":"calendar-state.json","stateSha256":"d7dd97bf32a26eb2868bfbef7d0c90e298c0d56c1d43a833d80c126801e54b88"});
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
