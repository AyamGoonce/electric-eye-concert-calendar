(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e7ad8cb6f6510379.js","sha256":"e7ad8cb6f6510379abe56b149b27f3d7da890a450ab3962fb04f6024194f5c1b","count":2252,"publishedAt":"2026-09-03T00:18:17Z","state":"calendar-state.json","stateSha256":"120b0ae83723663d41a5a8eace6ae98a240862d8b5103fd36f14d609a460d7d6"});
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
