(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.96bf875219a3ecc1.js","sha256":"96bf875219a3ecc1dab3ac88745389b06fb233e54124855c347560fa30a4a606","count":2501,"publishedAt":"2026-09-08T16:45:20Z","state":"calendar-state.json","stateSha256":"176aa1a4450350fb3a15f60f86c41e0ec09c7a131a10819bddcd64badcc7cd05"});
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
