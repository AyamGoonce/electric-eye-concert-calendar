(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cdccab83872405a7.js","sha256":"cdccab83872405a71a24f451006bc4c9e10ccb80917229e0815963e3c967571e","count":2137,"publishedAt":"2026-09-21T13:04:37Z","state":"calendar-state.json","stateSha256":"062de1271bc705d84b2f991c7481b780a60e22650ce36d17216c40813701baae"});
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
