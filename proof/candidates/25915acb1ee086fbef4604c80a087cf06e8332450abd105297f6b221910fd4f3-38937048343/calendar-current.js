(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.25915acb1ee086fb.js","sha256":"25915acb1ee086fbef4604c80a087cf06e8332450abd105297f6b221910fd4f3","count":2133,"publishedAt":"2026-10-16T17:08:39Z","state":"calendar-state.json","stateSha256":"2eab35e4a0ec402741e358ea28993bedda7d8f82720f8346487cf4ec228c7f4f","sourceState":"calendar-source-state.json","sourceStateSha256":"f583a3f4173eb203de325e613abe80a8feb553d55b829321b0a21e2a15dacc03"});
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
