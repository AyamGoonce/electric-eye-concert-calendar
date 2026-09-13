(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.24a1cc3f294a1e1a.js","sha256":"24a1cc3f294a1e1a9917a8f465ca12a08c8d850252f68a7e2d6d020763be72d7","count":2440,"publishedAt":"2026-09-13T23:16:20Z","state":"calendar-state.json","stateSha256":"a56b525e4066e03a346ad9f26a2a77a2e7e0de871853e0ef06a6a2b22d48d142"});
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
