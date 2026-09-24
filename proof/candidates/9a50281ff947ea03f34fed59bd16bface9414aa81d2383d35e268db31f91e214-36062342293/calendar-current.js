(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9a50281ff947ea03.js","sha256":"9a50281ff947ea03f34fed59bd16bface9414aa81d2383d35e268db31f91e214","count":2143,"publishedAt":"2026-09-24T21:34:51Z","state":"calendar-state.json","stateSha256":"095d4298b9ab05c68e39ad59a1f74df6e46b7cc41fedab31fc0145bccc259006","sourceState":"calendar-source-state.json","sourceStateSha256":"340649cb85922fe920783e88105c1838c6251eed876e896374091b44d54c1053"});
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
