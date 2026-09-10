(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b1d6e8285dd0bbd4.js","sha256":"b1d6e8285dd0bbd406db7352a32d568c543d83e7fb1fae7e823e32217cd77244","count":2497,"publishedAt":"2026-09-10T16:32:40Z","state":"calendar-state.json","stateSha256":"684718272bab65127f6f26fa21c9a9c445224b7621d5db645d40a8425f5b06fa"});
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
