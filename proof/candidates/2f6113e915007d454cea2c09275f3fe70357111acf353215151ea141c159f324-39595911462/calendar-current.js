(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2f6113e915007d45.js","sha256":"2f6113e915007d454cea2c09275f3fe70357111acf353215151ea141c159f324","count":2070,"publishedAt":"2026-10-21T12:00:01Z","state":"calendar-state.json","stateSha256":"882856064f5cf1134d63ffcee735de4d2660c5c87585b1ebc3ff19af0899e195","sourceState":"calendar-source-state.json","sourceStateSha256":"421a2ac5173837d24c1390e21262770fd5919476289b8e169eac973e90fe50ab"});
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
