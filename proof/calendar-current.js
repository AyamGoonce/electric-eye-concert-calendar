(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.66d2bed75e3b0c85.js","sha256":"66d2bed75e3b0c854cfcb1d473af92da9e4dea0d6e4b8edc5ba427ef9276f6c0","count":1726,"publishedAt":"2026-08-23T21:52:57Z","state":"calendar-state.json","stateSha256":"ef9de6fd86ad0fd5681ec0c3e43e9bc36391d63ca96123ef12cd9dfe98f3933c"});
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
