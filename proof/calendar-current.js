(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b9275d07442172d8.js","sha256":"b9275d07442172d8f77456bb627fabb267176f00d530c993048be6adac207a43","count":2521,"publishedAt":"2026-09-05T23:06:58Z","state":"calendar-state.json","stateSha256":"b50d52e1914e87fbd6bcc8dcf220f7a91a21724b36e0969e4c9715e3878eb5bb"});
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
