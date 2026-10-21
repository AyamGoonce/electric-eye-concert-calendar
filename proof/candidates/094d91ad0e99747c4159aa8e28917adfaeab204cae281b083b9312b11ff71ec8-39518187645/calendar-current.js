(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.094d91ad0e99747c.js","sha256":"094d91ad0e99747c4159aa8e28917adfaeab204cae281b083b9312b11ff71ec8","count":2055,"publishedAt":"2026-10-20T23:58:37Z","state":"calendar-state.json","stateSha256":"f6e76c578b8c7211bc59ee55649f60d19d9b694926d8e5654c452445a3815ff6","sourceState":"calendar-source-state.json","sourceStateSha256":"5b1568844e987272f6a25ab87640f809c8afed30c83a24de46955667c9ebf437"});
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
