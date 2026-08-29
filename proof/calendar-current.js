(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.446621306715abda.js","sha256":"446621306715abdaed79f56075b2792b58cfd284fd007b37326f12ff66e2846f","count":2064,"publishedAt":"2026-08-29T10:35:24Z","state":"calendar-state.json","stateSha256":"d84135a94d77d87d7fe9796c280885da441f0175110b5a8f9381081cd9dfe735"});
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
