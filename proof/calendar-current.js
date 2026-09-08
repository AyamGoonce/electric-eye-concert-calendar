(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.89b3ea7c12853c78.js","sha256":"89b3ea7c12853c7889d564a50eabb7bd742daea1575622d855b156d8423e2898","count":2497,"publishedAt":"2026-09-08T16:33:21Z","state":"calendar-state.json","stateSha256":"27059a72f4215b888934317fa4d9a30c749433f987b3d501cd433465d6c4aeb2"});
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
