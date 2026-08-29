(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.64208810aad63305.js","sha256":"64208810aad633056b6bd608ea7f55405b62fdcf355f35bdd3a21dec8a946208","count":2065,"publishedAt":"2026-08-29T00:47:30Z","state":"calendar-state.json","stateSha256":"3fd4f7ccc02a57fc040cf06f0577bb5b1c5878dd9e0818e6bf26f48aa545ed54"});
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
