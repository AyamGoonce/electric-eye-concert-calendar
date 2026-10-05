(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a90233c6a1ddb0d3.js","sha256":"a90233c6a1ddb0d3b8d228bfcc8bddc3cf23def17c380167c70d367cea5ee727","count":2147,"publishedAt":"2026-10-05T00:00:03Z","state":"calendar-state.json","stateSha256":"c9d0d6c4eecc94521dfb124e80639d684b62a25432dad0c735f95d52fe45e28f","sourceState":"calendar-source-state.json","sourceStateSha256":"d2d9868d0a56bec45833bfd9f602d7084b3280b30d7bdda52af09f596429a6b0"});
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
