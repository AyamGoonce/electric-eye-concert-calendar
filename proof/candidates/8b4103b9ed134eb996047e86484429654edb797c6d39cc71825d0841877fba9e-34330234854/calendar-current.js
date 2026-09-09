(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8b4103b9ed134eb9.js","sha256":"8b4103b9ed134eb996047e86484429654edb797c6d39cc71825d0841877fba9e","count":2491,"publishedAt":"2026-09-09T08:42:36Z","state":"calendar-state.json","stateSha256":"b246b73e4a2050e0fe5a4298c897d503b874ad9c68ddadff831662393e3f184e"});
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
