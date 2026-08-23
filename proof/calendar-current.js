(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.075d202d831cee35.js","sha256":"075d202d831cee35b96d2f062fd801b3465f318cc936ee96be7daaf1adca8015","count":1741,"publishedAt":"2026-08-23T18:54:08Z","state":"calendar-state.json","stateSha256":"1e79eecca262a0849c1ff56b637ed383cab363e34649d0ca960141fe0a127717"});
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
