(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5445906da40de44d.js","sha256":"5445906da40de44dd49fbe5b03ed89d992a73c77da9059206a72025fcde4e9de","count":2084,"publishedAt":"2026-11-23T00:19:30Z","state":"calendar-state.json","stateSha256":"6c1e11aa3658e58cb3319d72fe22373dbec6c0013b930c3f5d3ead685064c9f2","sourceState":"calendar-source-state.json","sourceStateSha256":"b0d113c810d1c70545a6a1fee8b2be65c6e5449203160995e35f8c3fe95f30a0"});
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
