(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6d5436bd991fbfac.js","sha256":"6d5436bd991fbfac956f7c4923f9b8c905c4686eead4333d801eca785ffc292e","count":2080,"publishedAt":"2026-08-31T23:02:20Z","state":"calendar-state.json","stateSha256":"3c4e019b14d5a3b98243eb38bf102bf182a0f4347c40e2f2a28bb0040566b89f"});
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
