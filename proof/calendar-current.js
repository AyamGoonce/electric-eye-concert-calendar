(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8e802606ba4bd94a.js","sha256":"8e802606ba4bd94af3eb2b5ef5ec83c39b04f1c57dcd6ef19d6ea37e5d5594d9","count":2095,"publishedAt":"2026-10-17T20:42:50Z","state":"calendar-state.json","stateSha256":"2bd07df747dc532461d005a50b9e654f0c3c80e36bb35ada8fbf2d27af96518c","sourceState":"calendar-source-state.json","sourceStateSha256":"79ea69149ef2324837375d840d07cd3a8cc693e3f3bdc2b2a996693c749992fa"});
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
