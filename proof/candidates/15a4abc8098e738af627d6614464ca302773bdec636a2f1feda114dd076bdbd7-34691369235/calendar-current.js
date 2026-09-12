(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.15a4abc8098e738a.js","sha256":"15a4abc8098e738af627d6614464ca302773bdec636a2f1feda114dd076bdbd7","count":2479,"publishedAt":"2026-09-12T11:38:52Z","state":"calendar-state.json","stateSha256":"5cdf84a74d63ffee5e67c797d24736b648e9dda820f15abbd1046815c93fd278"});
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
