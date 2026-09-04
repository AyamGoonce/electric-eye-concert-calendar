(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.aa8a2b96a4e8dd41.js","sha256":"aa8a2b96a4e8dd41ea6a30921a4f0d7d744c9cef36fd2421a2da3017fadc5567","count":2535,"publishedAt":"2026-09-04T16:36:41Z","state":"calendar-state.json","stateSha256":"dbc42ca38a916edf689241eaa46d67aaf0cc36f0c3936733e723ff20df4e981b"});
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
