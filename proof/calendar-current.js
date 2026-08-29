(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.042ec78a8050e58d.js","sha256":"042ec78a8050e58d3ebb99c84058368ffeedb3a748e4087dda56ad41cccaef0e","count":2065,"publishedAt":"2026-08-29T07:16:25Z","state":"calendar-state.json","stateSha256":"e0c1d7b70d7787733dc865c161262a8f17af508aa101447d985bbe8ad468c9da"});
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
