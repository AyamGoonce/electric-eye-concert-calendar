(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.72d76a5eb4c3d3c1.js","sha256":"72d76a5eb4c3d3c12587e71bf550abbb052d93eca90768ef7e9b049c1cab1641","count":2103,"publishedAt":"2026-10-17T10:54:17Z","state":"calendar-state.json","stateSha256":"476cf1582b1951a88849ee267669ba2df71e45b9dce67bf40b98ea19bf34c9fd","sourceState":"calendar-source-state.json","sourceStateSha256":"7836d6b9b9afa389bf1758ae0fcb1db1e376740945e95a84f064ba390abb147e"});
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
