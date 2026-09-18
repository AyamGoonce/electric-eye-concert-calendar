(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.78bb9f693e644fd1.js","sha256":"78bb9f693e644fd171932accc2a624c67d32df6f304a6e49519298ce05477bfa","count":2490,"publishedAt":"2026-09-18T04:53:33Z","state":"calendar-state.json","stateSha256":"71151f30928cc59aa9125bb2ac0c22186f3a133849d45d687c904e8d74465b25"});
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
